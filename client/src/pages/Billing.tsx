import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { Loader2, Lock, CheckCircle, AlertCircle, CreditCard, Calendar, User } from 'lucide-react';

interface IFormInput {
  cardholderName: string;
  cardNumber: string;
  expiryDate: string;
  cvc: string;
}

const Billing: React.FC = () => {
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<IFormInput>();
  const onSubmit: SubmitHandler<IFormInput> = async (data) => {
    try {
      const response = await fetch('/api/v1/billing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        setStatus({ type: 'success', message: 'Payment method added successfully' });
      } else {
        setStatus({ type: 'error', message: 'Failed to add payment method' });
      }
    } catch (error) {
      console.error('Error adding payment method:', error);
      setStatus({ type: 'error', message: 'An error occurred while adding the payment method' });
    }
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Billing</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Add a Payment Method</h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-4">
            <label htmlFor="cardholderName" className="block text-gray-700 font-medium mb-2">
              Cardholder Name <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" aria-hidden="true" />
              <input
                id="cardholderName"
                autoComplete="cc-name"
                className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.cardholderName ? 'border-red-500' : 'border-gray-300'}`}
                aria-invalid={!!errors.cardholderName}
                aria-describedby={errors.cardholderName ? "cardholderName-error" : undefined}
                {...register("cardholderName", { required: "Cardholder name is required" })}
              />
            </div>
            {errors.cardholderName && (
              <p id="cardholderName-error" className="text-red-500 text-sm mt-1" role="alert">
                {errors.cardholderName.message}
              </p>
            )}
          </div>
          <div className="mb-4">
            <label htmlFor="cardNumber" className="block text-gray-700 font-medium mb-2">
              Card Number <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <div className="relative">
              <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" aria-hidden="true" />
              <input
                id="cardNumber"
                type="text"
                inputMode="numeric"
                autoComplete="cc-number"
                placeholder="0000 0000 0000 0000"
                className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.cardNumber ? 'border-red-500' : 'border-gray-300'}`}
                aria-invalid={!!errors.cardNumber}
                aria-describedby={errors.cardNumber ? "cardNumber-error" : undefined}
                {...register("cardNumber", { required: "Card number is required" })}
              />
            </div>
            {errors.cardNumber && (
              <p id="cardNumber-error" className="text-red-500 text-sm mt-1" role="alert">
                {errors.cardNumber.message}
              </p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="expiryDate" className="block text-gray-700 font-medium mb-2">
                Expiry Date (MM/YY) <span className="text-red-500" aria-hidden="true">*</span>
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" aria-hidden="true" />
                <input
                  id="expiryDate"
                  type="text"
                  inputMode="numeric"
                  autoComplete="cc-exp"
                  placeholder="MM/YY"
                  className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.expiryDate ? 'border-red-500' : 'border-gray-300'}`}
                  aria-invalid={!!errors.expiryDate}
                  aria-describedby={errors.expiryDate ? "expiryDate-error" : undefined}
                  {...register("expiryDate", { required: "Expiry date is required" })}
                />
              </div>
              {errors.expiryDate && (
                <p id="expiryDate-error" className="text-red-500 text-sm mt-1" role="alert">
                  {errors.expiryDate.message}
                </p>
              )}
            </div>
            <div>
              <label htmlFor="cvc" className="block text-gray-700 font-medium mb-2">
                CVC <span className="text-red-500" aria-hidden="true">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" aria-hidden="true" />
                <input
                  id="cvc"
                  type="text"
                  inputMode="numeric"
                  autoComplete="cc-csc"
                  maxLength={4}
                  placeholder="123"
                  className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.cvc ? 'border-red-500' : 'border-gray-300'}`}
                  aria-invalid={!!errors.cvc}
                  aria-describedby={errors.cvc ? "cvc-error" : undefined}
                  {...register("cvc", { required: "CVC is required" })}
                />
              </div>
              {errors.cvc && (
                <p id="cvc-error" className="text-red-500 text-sm mt-1" role="alert">
                  {errors.cvc.message}
                </p>
              )}
            </div>
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 w-full disabled:opacity-70 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-live="polite"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" aria-hidden="true" />
                <span>Add Payment Method</span>
              </>
            )}
          </button>
        </form>
        {status && (
          <div
            className={`mt-4 p-4 rounded-lg flex items-start gap-3 ${status.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}
            role={status.type === 'error' ? 'alert' : 'status'}
            aria-live="polite"
          >
            {status.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 shrink-0" aria-hidden="true" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 shrink-0" aria-hidden="true" />
            )}
            <div>
              <span className="sr-only">{status.type === 'success' ? 'Success: ' : 'Error: '}</span>
              {status.message}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Billing;
