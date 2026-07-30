import { useParams } from "react-router-dom";


function Result(){

  const {jobId} = useParams();


  return (

    <div className="
      min-h-screen
      flex
      justify-center
      items-center
      px-6
    ">


      <div className="
        max-w-3xl
        w-full
        p-8
        border
        rounded-xl
        shadow-lg
      ">


        <h1 className="
          text-3xl
          font-bold
          text-center
        ">
          Your Meme Video is Ready 🎉
        </h1>



        <video

          controls

          className="
            mt-8
            w-full
            rounded-lg
          "

        >

          <source
            src={`http://localhost:8000/videos/${jobId}.mp4`}
            type="video/mp4"
          />

        </video>



        <a

          href={`http://localhost:8000/videos/${jobId}.mp4`}

          download

          className="
            block
            text-center
            mt-6
            bg-black
            text-white
            py-3
            rounded-lg
          "

        >
          Download Video

        </a>


      </div>


    </div>

  );

}


export default Result;