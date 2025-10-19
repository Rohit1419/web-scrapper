import React, { useState, useEffect } from "react";
import { Search, AlertCircle } from "lucide-react";
import { apiService } from "../api";
import { CASE_TYPES } from "../constant";
import LoadingSpinner from "./LoadingSpinner";

const CourtSelector = ({ onSubmit, disabled }) => {
  const [courts, setCourts] = useState([]);
  const [selectedCourt, setSelectedCourt] = useState("");
  const [date, setDate] = useState("");
  const [caseType, setCaseType] = useState("civil");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCourts();
  }, []);

  const loadCourts = async () => {
    try {
      setLoading(true);
      const courtsData = await apiService.getCourts();
      setCourts(courtsData);
    } catch (err) {
      setError("Failed to load courts");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!selectedCourt || !date) {
      setError("Please select a court and date");
      return;
    }

    setError("");
    onSubmit({
      court_index: parseInt(selectedCourt),
      date,
      case_type: caseType,
    });
  };

  if (loading) {
    return <LoadingSpinner message="Loading courts..." />;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Scraping Configuration
      </h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Court Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Court
          </label>
          <select
            value={selectedCourt}
            onChange={(e) => setSelectedCourt(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={disabled}
            required
          >
            <option value="">Choose a court...</option>
            {courts.map((court) => (
              <option key={court.index} value={court.index}>
                {court.name}
              </option>
            ))}
          </select>
        </div>

        {/* Date Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={disabled}
              required
            />
          </div>

          {/* Case Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Case Type
            </label>
            <select
              value={caseType}
              onChange={(e) => setCaseType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={disabled}
            >
              {CASE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={disabled || !selectedCourt || !date}
          className="w-full bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
        >
          <Search className="w-5 h-5 mr-2" />
          Start Scraping
        </button>
      </form>
    </div>
  );
};

export default CourtSelector;
