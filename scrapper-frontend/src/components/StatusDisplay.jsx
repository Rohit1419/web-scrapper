import React from "react";
import { Clock, CheckCircle, AlertCircle, XCircle } from "lucide-react";
import { STATUS_TYPES } from "../constant";

const StatusDisplay = ({ status }) => {
  const getStatusConfig = () => {
    switch (status.status) {
      case STATUS_TYPES.PENDING:
      case STATUS_TYPES.INITIALIZING:
      case STATUS_TYPES.PROCESSING:
        return {
          icon: <Clock className="w-5 h-5 text-blue-500 animate-spin" />,
          bgColor: "bg-blue-50",
          borderColor: "border-blue-200",
          textColor: "text-blue-800",
        };
      case STATUS_TYPES.CAPTCHA_REQUIRED:
        return {
          icon: <AlertCircle className="w-5 h-5 text-yellow-600" />,
          bgColor: "bg-yellow-50",
          borderColor: "border-yellow-200",
          textColor: "text-yellow-800",
        };
      case STATUS_TYPES.COMPLETED:
        return {
          icon: <CheckCircle className="w-5 h-5 text-green-600" />,
          bgColor: "bg-green-50",
          borderColor: "border-green-200",
          textColor: "text-green-800",
        };
      case STATUS_TYPES.ERROR:
        return {
          icon: <XCircle className="w-5 h-5 text-red-600" />,
          bgColor: "bg-red-50",
          borderColor: "border-red-200",
          textColor: "text-red-800",
        };
      default:
        return {
          icon: <Clock className="w-5 h-5 text-gray-500" />,
          bgColor: "bg-gray-50",
          borderColor: "border-gray-200",
          textColor: "text-gray-800",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div
      className={`${config.bgColor} ${config.borderColor} border rounded-lg p-4`}
    >
      <div className="flex items-center mb-2">
        {config.icon}
        <span className={`ml-2 font-medium ${config.textColor} capitalize`}>
          {status.status.replace("_", " ")}
        </span>
      </div>
      <p className={`${config.textColor.replace("800", "700")}`}>
        {status.message}
      </p>
    </div>
  );
};

export default StatusDisplay;
