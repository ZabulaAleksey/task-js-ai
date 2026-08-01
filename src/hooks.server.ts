import type { HandleServerError } from "@sveltejs/kit";

export const handleError: HandleServerError = ({
  error,
  event,
  status,
  message,
}) => {
  const errorId = crypto.randomUUID();
  console.error("Unhandled application error", {
    errorId,
    method: event.request.method,
    path: event.url.pathname,
    status,
    error,
  });

  return {
    message:
      status === 404
        ? message
        : "The application could not complete the request.",
    errorId,
  };
};
