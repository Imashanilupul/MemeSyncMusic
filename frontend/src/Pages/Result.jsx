import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

function Result() {
  const { jobId } = useParams();

  const [workflowData, setWorkflowData] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    const raw = sessionStorage.getItem(`meme-workflow-${jobId}`);

    if (!raw) {
      return;
    }

    try {
      setWorkflowData(JSON.parse(raw));
    } catch (error) {
      console.log(error);
    }
  }, [jobId]);

  const slides = useMemo(() => {
    if (!workflowData?.slides) {
      return [];
    }

    return [...workflowData.slides].sort((a, b) => a.start - b.start);
  }, [workflowData]);

  const activeSlide = useMemo(() => {
    if (!slides.length) {
      return null;
    }

    const currentSlide =
      slides.find((slide) => {
        const start = Number(slide.start) || 0;
        const end = start + (Number(slide.duration) || 0);
        return currentTime >= start && currentTime < end;
      }) || slides[slides.length - 1];

    return currentSlide;
  }, [currentTime, slides]);

  if (!workflowData) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="max-w-xl w-full p-8 border rounded-xl shadow-lg text-center">
          <h1 className="text-2xl font-bold">No generated result found</h1>
          <p className="text-gray-600 mt-3">
            Please generate a meme slideshow first from YouTube or upload flow.
          </p>
          <Link
            to="/upload"
            className="inline-block mt-6 bg-black text-white px-5 py-3 rounded-lg"
          >
            Go to Upload
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="max-w-4xl mx-auto p-8 border rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center">
          Your Meme Slideshow is Ready 🎉
        </h1>

        <p className="text-center text-gray-600 mt-3">
          Job: <span className="text-sm">{jobId}</span>
        </p>

        <div className="mt-8">
          <audio
            controls
            className="w-full"
            src={workflowData.audio_url}
            onTimeUpdate={(event) => {
              setCurrentTime(event.currentTarget.currentTime);
            }}
          />
        </div>

        <div className="mt-8 border rounded-lg p-4">
          <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
            {activeSlide?.image_url ? (
              <img
                src={activeSlide.image_url}
                alt="Matched meme"
                className="w-full h-full object-cover"
              />
            ) : (
              <p className="text-gray-500">No meme image available</p>
            )}
          </div>

          <div className="mt-4 text-center">
            <p className="text-lg font-semibold">
              {activeSlide?.text || "Waiting for playback..."}
            </p>
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-3">Timeline</h2>
          <div className="max-h-64 overflow-auto border rounded-lg">
            {slides.map((slide, index) => (
              <div
                key={`${slide.start}-${index}`}
                className={`p-3 border-b ${
                  activeSlide === slide ? "bg-gray-100" : ""
                }`}
              >
                <p className="text-sm text-gray-500">
                  {Number(slide.start).toFixed(2)}s -{" "}
                  {(Number(slide.start) + Number(slide.duration)).toFixed(2)}s
                </p>
                <p>{slide.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Result;
