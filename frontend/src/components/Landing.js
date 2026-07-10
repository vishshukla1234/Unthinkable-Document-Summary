import React, { useCallback, useState } from "react";
import "../App.css"
import FileUpload from "./FileUpload";
import SummaryOptions from "./SummaryOptions";
import SummaryDisplay from "./SummaryDisplay";
import Loading from "./Loading";
import { processDocument, summarizeText } from "../api";

export default function Landing() {
    const [length, setLength] = useState("medium");
    const [rawText, setRawText] = useState("");
    const [result, setResult] = useState(null);
    const [fileMeta, setFileMeta] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingLabel, setLoadingLabel] = useState("");
    const [error, setError] = useState("");

    const handleFileSelected = useCallback(async (file) => {
        setError("");
        setResult(null);
        setLoading(true);
        setLoadingLabel(
            /\.(png|jpe?g|tiff|bmp|webp)$/i.test(file.name)
                ? "Running OCR on your image..."
                : "Extracting text from your document..."
        );
        try {
            const data = await processDocument(file, length);
            setResult(data);
            setRawText(data.text);
            setFileMeta({ name: file.name });
        } catch (err) {
            setError(err.message || "Something went wrong while processing the document.");
        } finally {
            setLoading(false);
            setLoadingLabel("");
        }
    }, [length]);

    const handleLengthChange = useCallback(
        async (newLength) => {
            setLength(newLength);
            if (!rawText) return;
            setLoading(true);
            setLoadingLabel("Re-generating summary...");
            setError("");
            try {
                const data = await summarizeText(rawText, newLength);
                setResult((prev) => (prev ? { ...prev, ...data } : prev));
            } catch (err) {
                setError(err.message || "Could not regenerate the summary.");
            } finally {
                setLoading(false);
                setLoadingLabel("");
            }
        },
        [rawText]
    );

    const handleReset = () => {
        setResult(null);
        setRawText("");
        setFileMeta(null);
        setError("");
    };

    return (
        <div className="app">
            <header className="app-header">
                <div className="app-header__inner">
                    <div className="brand">
                        <span className="brand__mark">DS</span>
                        <span className="brand__name">Document Summary Assistant</span>
                    </div>
                    {result && (
                        <button className="btn-secondary" onClick={handleReset}>
                            New Document
                        </button>
                    )}
                </div>
            </header>

            <main className="app-main">
                {!result && (
                    <section className="hero">
                        <h1>Turn any document into a clear, smart summary</h1>
                        <p className="hero__subtitle">
                            Upload a PDF or a scanned image. Text is extracted, summarized, and
                            analyzed for improvement suggestions -- all processed locally, no
                            third-party AI API involved.
                        </p>
                    </section>
                )}

                <section className="options-section">
                    <h3 className="section-label">Summary length</h3>
                    <SummaryOptions value={length} onChange={handleLengthChange} disabled={loading} />
                </section>

                {!result && !loading && (
                    <FileUpload onFileSelected={handleFileSelected} disabled={loading} />
                )}

                {loading && <Loading label={loadingLabel} />}

                {error && (
                    <div className="error-banner" role="alert">
                        {error}
                    </div>
                )}

                {result && !loading && <SummaryDisplay result={result} />}
            </main>

            <footer className="app-footer">
                <span>Document Summary Assistant &mdash; by Vishal Shukla.</span>
            </footer>
        </div>
    );
}