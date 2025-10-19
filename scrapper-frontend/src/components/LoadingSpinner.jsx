import React from "react";
import { Clock } from "lucide-react";

const LoadingSpinner = ({ message = "Loading..." }) => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <Clock className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-2" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
