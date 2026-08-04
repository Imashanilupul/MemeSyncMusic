function Gallery(){

  const videos = [];


  return (

    <div className="
      min-h-screen
      p-10
    ">


      <h1 className="
        text-4xl
        font-bold
      ">
        My Meme Videos 🎞️
      </h1>



      {
        videos.length === 0 ? (

          <p className="mt-8 text-gray-600">
            No videos generated yet.
          </p>

        ):(

          <div>
            {
              videos.map((video)=>(
                <div key={video.id}>
                  {video.name}
                </div>
              ))
            }
          </div>

        )
      }


    </div>

  );

}


export default Gallery;