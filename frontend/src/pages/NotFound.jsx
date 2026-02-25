import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-base-200 px-4 text-center">
      <div className="max-w-md">
        <h1 className="text-9xl font-extrabold text-primary mb-4">404</h1>
        <h2 className="text-3xl font-bold mb-6">Page Not Found</h2>
        <p className="text-base-content/70 mb-8">
          Oops! The page you are looking for doesn't exist, has been moved, or you don't have permission to view it.
        </p>
        <Link to="/" className="btn btn-primary">
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}

export default NotFound;