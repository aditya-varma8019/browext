document.addEventListener('DOMContentLoaded', function () {
    var detectButton = document.getElementById('detectObjects');
    var resultDiv = document.getElementById('result');

    detectButton.addEventListener('click', function () {
        resultDiv.textContent = 'Detecting objects...';

        fetch('http://localhost:5000/detect', {
            method: 'POST'
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
                var a = document.createElement('a');
                var img = document.createElement('img');
                img.src = 'data:image/jpeg;base64,' + obj.image;
                img.style.width = '100px';  // Set the desired width
                a.href = obj.amazon_link;
                a.target = '_blank';
                a.appendChild(img);
                li.appendChild(a);
                ul.appendChild(li);
            });
            resultDiv.appendChild(ul);
        }
    }
});
