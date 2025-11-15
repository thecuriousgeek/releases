function PopupOpen(pTitle,pURL) {
  _ModalContent = document.getElementById("ModalContent");
  if (_ModalContent!=null)
    _ModalContent.parentElement.removeChild(_ModalContent);
  _ModalContent = document.createElement("div");
  _ModalContent.id = "ModalContent";
  _ModalContent.className = "modal-content";
  _ModalContent.tabindex = 1;
  window.top.document.body.appendChild(_ModalContent);
  _ModalTitleBar = document.createElement("div");
  _ModalTitleBar.className = "modal-title";
  _ModalContent.appendChild(_ModalTitleBar);
  _ModalTitle = document.createElement("span");
  _ModalTitleBar.appendChild(_ModalTitle);
  _ModalClose = document.createElement("span");
  _ModalClose.className = "modal-close";
  _ModalClose.innerHTML = "&times;";
  _ModalClose.onclick = function(){PopupClose();}
  _ModalTitleBar.appendChild(_ModalClose);
  _ModalFrame = document.createElement("iframe");
  _ModalFrame.className = "modal-frame";
  _ModalFrame.id = "ModalFrame";
  _ModalContent.appendChild(_ModalFrame);
  _ModalFrame.src = pURL;
  _ModalTitle.textContent = pTitle;
  _ModalContent.style.display = "block";
  _ModalFrame.contentWindow.focus();
}
function PopupClose() {
  _ModalContent = document.getElementById("ModalContent");
  if (_ModalContent!=null && _ModalContent.style.display!="none") {//This is for my child modal window
    _ModalContent.style.display="none";
    _ModalContent.parentElement.removeChild(_ModalContent);
    console.log("Closing my child");
    return;
  }
  if (window.frameElement==null) return;
  console.log("Closing my parent's child");
  window.frameElement.parentElement.style.display = "none";
  window.frameElement.parentElement.parentElement.removeChild(window.frameElement.parentElement);
}
function PopupPosition(pContent) {
  if (window.frameElement==null) return;
  // window.frameElement.style.width = document.body.scrollWidth+30+'px';
  // window.frameElement.style.height = document.body.scrollHeight+50+'px';
  window.frameElement.parentElement.style.position = "fixed";
  window.frameElement.parentElement.style.top = "50%";
  window.frameElement.parentElement.style.left = "50%";
  window.frameElement.parentElement.style.transform = "translate(-50%, -50%)";
  window.frameElement.parentElement.style.width = Math.min(window.screen.availWidth,pContent.scrollWidth)+50+'px';
  window.frameElement.parentElement.style.height = Math.min(window.screen.availHeight,document.body.scrollHeight)+50+'px';
}
function Alert(pMethod,pURL) {
  fetch(pURL,{method:pMethod})
  .then(data=>{return data.text();})
  .then(text=>{alert(text);});
}
function KeyDown(pKeyCode) {
  var _Code;
  if (window.event)
    _Code = window.event.keyCode;
  else if (e)
    _Code = e.which;
  if (_Code==27)
    PopupClose();
}