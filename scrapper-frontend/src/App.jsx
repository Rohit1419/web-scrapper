import React from "react";
import { FileText, AlertCircle } from "lucide-react";
import { useScrapingSession } from "./hooks/userScrapingSession";
import { STATUS_TYPES } from "./constant";
import CourtSelector from "./components/CourtSelector";
import StatusDisplay from "./components/StatusDisplay";
import CaptchaPrompt from "./components/CaptchaPrompt";
import ResultDisplay from "./components/ResultDisplay";
import "./App.css";

function App() {
  const {
    session,
    status,
    loading,
    error,
    startScraping,
    confirmCaptcha,
    resetSession,
    setError,
  } = useScrapingSession();

  const handleStartScraping = (scrapeData) => {
    setError("");
    startScraping(scrapeData);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <FileText className="w-10 h-10 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-800">
              Delhi District Court Cause List Scraper
            </h1>
          </div>
          <p className="text-gray-600">
            Extract cause lists from Delhi District Courts and generate PDF
            reports
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              {error}
            </div>
          </div>
        )}

        <div className="space-y-6">
          {!session && !loading && (
            <CourtSelector onSubmit={handleStartScraping} disabled={loading} />
          )}

          {session && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Scraping Progress
              </h2>

              {status && <StatusDisplay status={status} />}

              {status?.status === STATUS_TYPES.CAPTCHA_REQUIRED && (
                <div className="mt-4">
                  <CaptchaPrompt onConfirm={confirmCaptcha} />
                </div>
              )}

              {status?.status === STATUS_TYPES.COMPLETED && (
                <div className="mt-6">
                  <ResultDisplay status={status} onReset={resetSession} />
                </div>
              )}

              {status?.status === STATUS_TYPES.ERROR && (
                <div className="mt-4">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <p className="text-red-700">Error: {status.message}</p>
                  </div>
                  <button
                    onClick={resetSession}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>
            <span className="font-bold">Try this out:</span>
            <br />
            Court = 52 Sh. Dharmender Rana...
            <br /> Date = 2025-10-16
            <br /> Case Type = Civil
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
