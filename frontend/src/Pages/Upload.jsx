import { useState } from "react";
import { processYouTube, uploadMusic } from "../Services/api";
import { useNavigate } from "react-router-dom";


function Upload() {

  const [file, setFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingMode, setLoadingMode] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const navigate = useNavigate();



  const handleUpload = async () => {

    if(!file){
      alert("Please select a music file");
      return;
    }


    const formData = new FormData();

    formData.append(
      "file",
      file
    );


    try {

      setLoading(true);
      setLoadingMode("upload");
      setErrorMessage("");


      const response = await uploadMusic(formData, (event) => {

        const percentage = Math.round(
          (event.loaded * 100) / event.total
        );

        setProgress(percentage);

      });


      const jobId = response.data.job_id;
      const filename = response.data.filename;


      navigate(
        `/processing?job=${jobId}&source=upload&audioFile=${encodeURIComponent(filename)}`
      );


    } catch(error){

      console.log(error);
      setErrorMessage(
        error.response?.data?.detail || "Upload failed."
      );

    }
    finally{

      setLoading(false);
      setLoadingMode("");

    }

  };

  const handleYouTubeProcess = async () => {

    if(!youtubeUrl.trim()){
      alert("Please enter a YouTube URL");
      return;
    }

    try{

      setLoading(true);
      setLoadingMode("youtube");
      setErrorMessage("");

      const response = await processYouTube(youtubeUrl.trim());
      const jobId = response.data.job_id;

      navigate(`/processing?job=${jobId}&source=youtube`);

    } catch(error){

      console.log(error);
      setErrorMessage(
        error.response?.data?.detail || "Failed to process YouTube URL."
      );

    } finally{

      setLoading(false);
      setLoadingMode("");

    }

  };



  return (

    <div className="
      min-h-screen 
      flex items-center justify-center
      px-6
    ">


      <div className="
        w-full max-w-lg
        p-8
        rounded-xl
        shadow-lg
        border
      ">


        <h1 className="
          text-3xl 
          font-bold
          text-center
        ">
          Upload Your Song 🎵
        </h1>


        <p className="
          text-center
          mt-3
          text-gray-600
        ">
          Paste a YouTube music URL or upload MP3/WAV to create a meme slideshow video.
        </p>


        <div className="mt-8 space-y-3">

          <label className="text-sm font-semibold">
            YouTube Music URL
          </label>

          <input
            className="
              w-full
              border
              p-3
              rounded-lg
            "
            type="text"
            placeholder="https://www.youtube.com/watch?v=..."
            value={youtubeUrl}
            onChange={(e)=>setYoutubeUrl(e.target.value)}
          />

          <button

            onClick={handleYouTubeProcess}

            disabled={loading}

            className="
              w-full
              bg-black
              text-white
              py-3
              rounded-lg
              hover:bg-gray-800
            "

          >
            {
              loading && loadingMode === "youtube"
              ? "Processing YouTube URL..."
              : "Generate from YouTube URL"
            }
          </button>
        </div>


        <div className="my-6 text-center text-gray-500">
          OR
        </div>


        <input
          className="
            w-full
            border
            p-3
            rounded-lg
          "

          type="file"

          accept=".mp3,.wav"

          onChange={(e)=>setFile(e.target.files[0])}

        />


        {
          file && (

            <p className="mt-3 text-sm">
              Selected:
              <b> {file.name}</b>
            </p>

          )
        }


        {
          progress > 0 && (

            <div className="mt-5">

              <progress
                value={progress}
                max="100"
                className="w-full"
              />

              <p className="text-center">
                {progress}%
              </p>

            </div>

          )
        }



        <button

          onClick={handleUpload}

          disabled={loading || !file}

          className="
            mt-6
            w-full
            bg-black
            text-white
            py-3
            rounded-lg
            hover:bg-gray-800
          "

        >

          {
            loading && loadingMode === "upload"
            ? "Uploading..."
            : "Generate Meme Video"
          }


        </button>

        {
          errorMessage && (
            <div className="mt-5 p-3 rounded-lg bg-red-50 text-red-700">
              {errorMessage}
            </div>
          )
        }


      </div>


    </div>

  );

}


export default Upload;