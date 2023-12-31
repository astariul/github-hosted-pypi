function openLinkInNewTab(link) {
  window.open(link, '_blank');
}

function load_readme(version, scroll_to_div=false){
  addDynamicClickDelegation(`${version}`);

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

function addDynamicClickDelegation(parentId) {
  const parentDiv = document.getElementById(parentId);

  if (parentDiv) {
      parentDiv.addEventListener('click', function (event) {
          if (event.target !== this) {
              event.stopPropagation();
              this.click(); // Trigger the parent div's onclick function
          }
      });
  }
}

function removeHrefFromAnchors() {
  var versionsSection = document.getElementById('versions');
  if (versionsSection) {
      var anchors = versionsSection.getElementsByTagName('a');
      for (var i = 0; i < anchors.length; i++) {
          anchors[i].removeAttribute('href');
      }
  }
}

window.onload = function() {
  removeHrefFromAnchors();
};
