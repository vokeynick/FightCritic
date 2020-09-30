<script>
        const form = document.querySelector('#post-form');

        // makes POST request to store blog post on form submit
        form.onsubmit = e => {
          e.preventDefault();
          fetch("/post", {
            method: 'POST',
            body: new FormData(form)
          })
          .then(r => {
            form.reset();
          });
        }

        // makes DELETE request to delete a post
        function deletePost(id) {
          fetch(`/post/${id}`, {
            method: 'DELETE'
          });
        }

        // makes PUT request to deactivate a post
        function deactivatePost(id) {
          fetch(`/post/${id}`, {
            method: 'PUT'
          });
        }

        // appends new posts to the list of blog posts on the page
        function appendToList(data) {
          const html = `
            <div class="card" id="${data.id}">
              <header class="card-header">
                <p class="card-header-title">${data.title}</p>
              </header>
              <div class="card-content">
                <div class="content">
                  <p>${data.content}</p>
                </div>
              </div>
              <footer class="card-footer">
                <a href="#" onclick="deactivatePost('${data.id}')" class="card-footer-item">Deactivate</a>
                <a href="#" onclick="deletePost('${data.id}')" class="card-footer-item">Delete</a>
              </footer>
            </div>`;
          let list = document.querySelector("#post-list")
          list.innerHTML += html;
        };
      </script>
