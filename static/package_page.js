function load_readme(version, scroll_to_div=false){
  let urlVersion = url_readme_main.replace('main', version);
  fetch(urlVersion)
  .then(response => {
      if (!response.ok) {
          if (response.status == 404) {
            return 'No README found for this version';
          }
          throw new Error(`Failed to fetch content. Status code: ${response.status}`);
      }
      return response.text();
  })
  .then(markupContent => {
    const contentDivs = document.querySelectorAll('.versions div');
    contentDivs.forEach(div => div.classList.remove('selected'));

    document.getElementById(version).classList.add('selected');
    document.getElementById('markdown-container').innerHTML = marked.parse(markupContent);
    if (scroll_to_div) {
      // document.getElementById('description_pkg').scrollIntoView();
      history.replaceState(null, null, '#'+version);
    }
  })
  .catch(error => {
      console.error('Error:', error.message);
  });
}

function warn_unsafe() {
  document.getElementById('installdanger').hidden = false;
  document.getElementById('installcmd').hidden = true;
}

function redirectToIndex() {
  window.location.href = "../index.html";
}


