import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 bg-red-50 text-red-900 h-full overflow-auto">
          <h1 className="text-2xl font-bold mb-4">Algo salió mal en esta página.</h1>
          <div className="mb-4">
            <p className="font-bold text-lg">{this.state.error && this.state.error.toString()}</p>
          </div>
          <details className="whitespace-pre-wrap">
            <summary className="cursor-pointer font-medium mb-2">Ver detalles técnicos</summary>
            <pre className="text-xs bg-white p-4 rounded border border-red-200 overflow-auto shadow-sm">
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </pre>
          </details>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
