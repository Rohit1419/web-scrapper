import React from "react";
import { AlertCircle } from "lucide-react";

const CaptchaPrompt = ({ onConfirm }) => {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div className="flex items-center mb-2">
        <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
        <span className="font-medium text-yellow-800">CAPTCHA Required</span>
      </div>
      <p className="text-yellow-700 mb-3">
        Please solve the CAPTCHA in the browser window that opened, then click
        the button below.
      </p>
      <button
        onClick={onConfirm}
        className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition-colors"
      >
        I've Solved the CAPTCHA
      </button>
    </div>
  );
};

export default CaptchaPrompt;
