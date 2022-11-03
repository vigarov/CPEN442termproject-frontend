
var initialNum = -1;

function msToTime(duration) {
    var seconds = Math.floor((duration / 1000) % 60),
      minutes = Math.floor((duration / (1000 * 60)) % 60);
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;
  
    return minutes + ":" + seconds ;
  }

//Called every 1000 ms; to in ms
function updateTimer(to) {
    let timeLeft = document.getElementById("timeLeft");
    let newContent = "";
    if(initialNum == 0) newContent = "Expired! Please login again through the homepage...";
    else{
        if(initialNum == -1) initialNum = to
        else initialNum-=1000;
        newContent = msToTime(initialNum);
    }
    timeLeft.innerHTML = newContent;
}