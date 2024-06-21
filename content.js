// let isSelecting = false;
// let startX, startY;
// let selectionDiv;

// function startSelection() {
//     isSelecting = true;
//     document.body.style.cursor = 'crosshair';

//     selectionDiv = document.createElement('div');
//     selectionDiv.style.position = 'fixed';
//     selectionDiv.style.border = '2px dashed red';
//     selectionDiv.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
//     selectionDiv.style.pointerEvents = 'none';
//     document.body.appendChild(selectionDiv);

//     document.addEventListener('mousedown', onMouseDown);
//     document.addEventListener('mousemove', onMouseMove);
//     document.addEventListener('mouseup', onMouseUp);
// }

// function onMouseDown(e) {
//     if (!isSelecting) return;
//     startX = e.clientX;
//     startY = e.clientY;
// }

// function onMouseMove(e) {
//     if (!isSelecting || !startX) return;
//     const width = Math.abs(e.clientX - startX);
//     const height = Math.abs(e.clientY - startY);
//     const left = Math.min(e.clientX, startX);
//     const top = Math.min(e.clientY, startY);

//     selectionDiv.style.width = width + 'px';
//     selectionDiv.style.height = height + 'px';
//     selectionDiv.style.left = left + 'px';
//     selectionDiv.style.top = top + 'px';
// }

// function onMouseUp(e) {
//     if (!isSelecting) return;
//     isSelecting = false;
//     document.body.style.cursor = 'default';

//     const width = Math.abs(e.clientX - startX);
//     const height = Math.abs(e.clientY - startY);
//     const left = Math.min(e.clientX, startX);
//     const top = Math.min(e.clientY, startY);

//     chrome.runtime.sendMessage({
//         action: "selectionMade",
//         selection: { left, top, width, height }
//     });

//     document.removeEventListener('mousedown', onMouseDown);
//     document.removeEventListener('mousemove', onMouseMove);
//     document.removeEventListener('mouseup', onMouseUp);
//     document.body.removeChild(selectionDiv);
// }

// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//     if (message.action === "startSelection") {
//         startSelection();
//     }
// });