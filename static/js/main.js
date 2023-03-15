function convertAbi(event) {
    event.preventDefault();
    let abi = document.getElementById("abi").value;
    let abi_type = document.getElementById("abi_type").value;
    let converted_abi = document.getElementById("converted_abi");

    converted_abi.value = "Converting ABI...";

    const formData = new FormData();
    formData.append("abi", abi);
    formData.append("abi_type", abi_type);

    fetch("/stream_abi", {
        method: "POST",
        body: formData
    })
    .then((response) => response.json())
    .then((data) => {
        converted_abi.value = data.converted_abi;
    })
    .catch(() => {
        converted_abi.value = "An error occurred.";
    });
}
