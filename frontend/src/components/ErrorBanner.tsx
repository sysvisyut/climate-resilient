type Props = { message: string; onClose?: () => void };

export default function ErrorBanner({ message, onClose }: Props) {
  return (
    <div role="alert" className="border border-red-200 bg-red-50 text-red-800 px-3 py-2 rounded-md flex items-center justify-between">
      <span>{message}</span>
      {onClose && (
        <button aria-label="Close error" onClick={onClose} className="ml-3 text-red-700 underline">Close</button>
      )}
    </div>
  );
}


