import { useState, useEffect, useCallback } from "react";
import { apiService } from "../api";
import { STATUS_TYPES } from "../constant";

export const useScrapingSession = () => {
  const [session, setSession] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let interval;

    if (session?.session_id) {
      interval = setInterval(async () => {
        try {
          const statusData = await apiService.getStatus(session.session_id);
          setStatus(statusData);

          if (
            [STATUS_TYPES.COMPLETED, STATUS_TYPES.ERROR].includes(
              statusData.status
            )
          ) {
            setLoading(false);
            clearInterval(interval);
          }
        } catch (err) {
          setError("Connection lost. Please try again.");
          clearInterval(interval);
        }
      }, 2000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [session?.session_id]);

  const startScraping = useCallback(async (scrapeData) => {
    setLoading(true);
    setError("");
    setStatus(null);

    try {
      const sessionData = await apiService.startScraping(scrapeData);
      setSession(sessionData);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start scraping");
      setLoading(false);
    }
  }, []);

  const confirmCaptcha = useCallback(async () => {
    if (!session?.session_id) return;

    try {
      await apiService.confirmCaptcha(session.session_id);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to confirm CAPTCHA");
    }
  }, [session?.session_id]);

  const resetSession = useCallback(() => {
    if (session?.session_id) {
      apiService.cancelSession(session.session_id).catch(console.error);
    }

    setSession(null);
    setStatus(null);
    setLoading(false);
    setError("");
  }, [session?.session_id]);

  return {
    session,
    status,
    loading,
    error,
    startScraping,
    confirmCaptcha,
    resetSession,
    setError,
  };
};
