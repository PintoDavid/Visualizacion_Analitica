document.getElementById('loadDataBtn').addEventListener('click', () => {
    const folderInput = document.getElementById('folderInput');
    if (folderInput.files.length === 0) {
        alert("Please select a folder with files.");
        return;
    }
    
    const folderPath = folderInput.files[0].webkitRelativePath.split("/")[0];
    fetch('/process-files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folderPath: folderPath })
    })
    .then(response => response.json())
    .then(data => {
        initialize3DVisualization(data);
    })
    .catch(error => console.error('Error:', error));
});

function initialize3DVisualization(data) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('visualization3D').appendChild(renderer.domElement);
    
    data.forEach((fileData, index) => {
        const geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array(fileData.data.flat());
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        const material = new THREE.PointsMaterial({ color: Math.random() * 0xffffff });
        const points = new THREE.Points(geometry, material);
        scene.add(points);
    });

    camera.position.z = 5;
    
    function animate() {
        requestAnimationFrame(animate);
        scene.rotation.x += 0.01;
        scene.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();
}
