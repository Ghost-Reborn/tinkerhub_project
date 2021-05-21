function make_toast(){
    var toast = document.getElementById("toast");
    toast.className = "show";
    setTimeout(function(){toast.className = toast.className.replace("show", "");}, 2500);
}