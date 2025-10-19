import React from "react";
import { Download, CheckCircle, RefreshCw, ExternalLink } from "lucide-react";
import { apiService } from "../api";

const ResultDisplay = ({ status, onReset }) => {
  const handleOpenPDF = () => {
    if (status?.pdf_url) {
      const downloadUrl = apiService.getDownloadUrl(status.pdf_url);
      window.open(downloadUrl, "_blank");
    }
  };

  const handleDownload = () => {
    if (status?.pdf_url) {
      const downloadUrl = apiService.getDownloadUrl(status.pdf_url);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = status.pdf_url.split("/").pop();
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center mb-2">
          <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
          <span className="font-medium text-green-800">
            Scraping Completed Successfully!
          </span>
        </div>
        <p className="text-green-700 mb-4">
          Cause list has been extracted and PDF has been generated.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          {status?.pdf_url && (
            <>
              <button
                onClick={handleOpenPDF}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center justify-center transition-colors"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Open PDF in New Tab
              </button>

              <button
                onClick={handleDownload}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center justify-center transition-colors"
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </button>
            </>
          )}

          <button
            onClick={onReset}
            className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 flex items-center justify-center transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Start New Search
          </button>
        </div>
      </div>

      {status?.tables && status.tables.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Preview ({status.tables.length} table
            {status.tables.length > 1 ? "s" : ""} found)
          </h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {status.tables.map((table, idx) => (
              <div key={idx} className="border rounded-lg overflow-hidden">
                <div className="bg-blue-50 px-4 py-2">
                  <h4 className="font-medium text-blue-800">{table.caption}</h4>
                  <p className="text-sm text-blue-600">
                    {table.rows?.length || 0} rows
                  </p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    {table.headers && table.headers.length > 0 && (
                      <thead className="bg-gray-50">
                        <tr>
                          {table.headers.map((header, hidx) => (
                            <th
                              key={hidx}
                              className="px-4 py-2 text-left font-medium text-gray-700 border-b"
                            >
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                    )}
                    <tbody>
                      {table.rows &&
                        table.rows.slice(0, 5).map((row, ridx) => (
                          <tr
                            key={ridx}
                            className={
                              ridx % 2 === 0 ? "bg-white" : "bg-gray-50"
                            }
                          >
                            {row.map((cell, cidx) => (
                              <td
                                key={cidx}
                                className="px-4 py-2 border-b text-xs"
                              >
                                {cell || "-"}
                              </td>
                            ))}
                          </tr>
                        ))}
                    </tbody>
                  </table>
                  {table.rows && table.rows.length > 5 && (
                    <div className="bg-gray-50 px-4 py-2 text-center text-gray-500 text-sm border-t">
                      ... and {table.rows.length - 5} more rows
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;
