export const API_BASE_URL = "http://localhost:8000";

export const STATUS_TYPES = {
  PENDING: "pending",
  INITIALIZING: "initializing",
  CAPTCHA_REQUIRED: "captcha_required",
  PROCESSING: "processing",
  COMPLETED: "completed",
  ERROR: "error",
};

export const CASE_TYPES = [
  { value: "civil", label: "Civil" },
  { value: "criminal", label: "Criminal" },
];
