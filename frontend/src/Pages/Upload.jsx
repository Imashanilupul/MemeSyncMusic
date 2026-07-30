import { useState } from "react";
import { uploadMusic } from "../Services/api";
import { useNavigate } from "react-router-dom";


function Upload() {

  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);

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


      const response = await uploadMusic(formData, (event) => {

        const percentage = Math.round(
          (event.loaded * 100) / event.total
        );

        setProgress(percentage);

      });


      const jobId = response.data.job_id;


      navigate(`/processing?job=${jobId}`);


    } catch(error){

      console.log(error);
      alert("Upload failed");

    }
    finally{

      setLoading(false);

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
          Upload MP3 or WAV and create your meme video.
        </p>



        <input
          className="
            mt-8
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

          disabled={loading}

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
            loading
            ? "Uploading..."
            : "Generate Meme Video"
          }


        </button>


      </div>


    </div>

  );

}


export default Upload;