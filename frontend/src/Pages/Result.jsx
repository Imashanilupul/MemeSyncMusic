import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

function Result() {
  const { jobId } = useParams();

  const [workflowData, setWorkflowData] = useState(null);

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

  const videoUrl = workflowData?.video_url || "";

  const handleDownloadVideo = () => {
    if (!videoUrl) {
      return;
    }

    const anchor = document.createElement("a");
    anchor.href = videoUrl;
    anchor.download = `${jobId || "meme-video"}.mp4`;
    anchor.target = "_blank";
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
  };

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
          Your Meme Video is Ready 🎉
        </h1>

        <p className="text-center text-gray-600 mt-3">
          Job: <span className="text-sm">{jobId}</span>
        </p>

        <div className="mt-8">
          {videoUrl ? (
            <video controls className="w-full rounded-lg border" src={videoUrl} />
          ) : (
            <div className="rounded-lg border border-dashed p-10 text-center text-gray-600">
              Preparing your generated video...
            </div>
          )}
        </div>

        {slides.length > 0 && (
          <p className="mt-4 text-center text-sm text-gray-600">
            {slides.length} slideshow scenes ready for playback.
          </p>
        )}

        {videoUrl && (
          <div className="mt-4 flex justify-center">
            <button
              type="button"
              onClick={handleDownloadVideo}
              className="bg-black text-white px-5 py-3 rounded-lg hover:bg-gray-800"
            >
              Download Combined Video
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Result;
