import { getContext, setContext } from "svelte";
import { translate, type TranslationKey } from "$lib/i18n";
import type { Language } from "$lib/types";

const localeContext = Symbol("locale");

export class LocaleState {
  language = $state<Language>("en");

  initialize() {
    const saved = localStorage.getItem("language");
    const detected = navigator.languages
      .map((value) => value.toLowerCase().split("-")[0])
      .find((value) => value === "en" || value === "ru" || value === "uk");
    this.setLanguage(
      saved === "en" || saved === "ru" || saved === "uk"
        ? saved
        : ((detected as Language | undefined) ?? "en"),
    );
  }

  setLanguage(language: Language) {
    this.language = language;
    if (typeof document !== "undefined") {
      document.documentElement.lang = language;
      localStorage.setItem("language", language);
    }
  }

  t(key: TranslationKey, values: Record<string, string> = {}) {
    return translate(this.language, key, values);
  }
}

export function provideLocaleState() {
  return setContext(localeContext, new LocaleState());
}

export function useLocaleState() {
  return getContext<LocaleState>(localeContext);
}
