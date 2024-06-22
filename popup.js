document.addEventListener('DOMContentLoaded', function () {
    var uploadInput = document.getElementById('uploadImage');
    var detectButton = document.getElementById('detectObjects');
    var resultDiv = document.getElementById('result');
    var uploadedFile;

    uploadInput.addEventListener('change', function (event) {
        uploadedFile = event.target.files[0];
        if (uploadedFile) {
            resultDiv.textContent = `Selected file: ${uploadedFile.name}`;
        }
    });

    detectButton.addEventListener('click', function () {
        if (!uploadedFile) {
            resultDiv.textContent = 'Please upload an image first.';
            return;
        }

        resultDiv.textContent = 'Detecting objects...';
        var formData = new FormData();
        formData.append('image', uploadedFile);

        fetch('http://localhost:5000/detect', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.textContent = 'Error: ' + data.error;
                } else {
                    displayResults(data.detected_objects);
                }
            })
            .catch(error => {
                resultDiv.textContent = 'Error: ' + error.message;
            });
    });

    function displayResults(objects) {
        resultDiv.innerHTML = '';
        if (objects.length === 0) {
            resultDiv.textContent = 'No objects detected.';
        } else {
            var ul = document.createElement('ul');
            objects.forEach(function (obj) {
                var li = document.createElement('li');
                var img = document.createElement('img');
                img.src = 'data:image/jpeg;base64,' + obj.image;
                img.style.width = '100px'; // Adjust the size as needed
                img.style.cursor = 'pointer';
                img.addEventListener('click', function () {
                    window.open(obj.amazon_link, '_blank');
                });
                li.appendChild(img);
                ul.appendChild(li);
            });
            resultDiv.appendChild(ul);
        }
    }
});
