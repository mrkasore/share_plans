document.addEventListener('DOMContentLoaded', function() {
    const csrftoken = getCookie('csrftoken');
    let input = document.getElementById("search-input");
    let suggestionsList = document.getElementById("suggestions-list");
    suggestionsList.innerHTML = ""; 
  
    input.addEventListener("input", function () {
      const query = input.value.trim();
      if (query.length > 0) {
        fetchSuggestions(query);
      } else {
        suggestionsList.innerHTML = "";
      }
    });
    
    changeMonth();
    editEvent(csrftoken);
    following(csrftoken);
    change_followers(csrftoken);
    search();
    delete_follower(csrftoken);

    if (document.getElementById('inp-year') && document.getElementById('inp-month')) {
        let year = document.getElementById('inp-year').value;
        let month = document.getElementById('inp-month').value;
        
        month = month.length == 1 ? '0' + month : month;
        document.querySelector('#monthInput').value = `${year}-${month}`;

        document.querySelector('#monthInput').addEventListener('change', () => {
            let month_input = document.querySelector('#monthInput').value.split('-');
            window.location.href = `?year=${month_input[0]}&month=${month_input[1]}`;
        });
    }

    if (document.getElementById('image')) {
        document.getElementById('image').addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('preview').src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

function fetchSuggestions(query) {
    let input_search = document.querySelector('[type="search"]').value;
    fetch(`/search?username=${input_search}`)
      .then((response) => response.json())
      .then((data) => {
        renderSuggestions(data.matching);
      })
      .catch((error) => {
        console.error("Error fetching suggestions:", error);
      });
}

function renderSuggestions(suggestions) {
    let input = document.getElementById("search-input");
    let suggestionsList = document.getElementById("suggestions-list");
    suggestionsList.innerHTML = "";
    suggestions.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      li.classList.add("list-group-item");
      li.addEventListener("click", () => {
        input.value = item;
        suggestionsList.innerHTML = "";
      });
      suggestionsList.appendChild(li);
    });
}

function following(csrftoken) {
    let follow_btn = document.querySelector('#following');

    if(follow_btn) {
        follow_btn.addEventListener('click', () => {
            fetch('/following', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    user_id: document.querySelector('#user_profile').getAttribute('data-user'),
                })
              })
                .then(response => response.json())
                .then(result => {
                    if (result.is_follower) {
                        follow_btn.innerHTML = 'Подписаться';
                        elUser = document.getElementById(result.user_id);
                        elUser.remove();
                    } else {
                        follow_btn.innerHTML = 'Отписаться';
                        let all_followers = document.querySelector('#all-followers');
                        let elUser = document.createElement('li');
                        elUser.setAttribute('id', result.user_id);
                        let elHref = document.createElement('a');
                        let url = `/profile/${result.user_id}`;
                        elHref.setAttribute('href', url);
                        elHref.innerHTML = result.username;
                        elUser.append(elHref);
                        all_followers.append(elUser);
                    }
                })
        });
    }
}

function changeMonth() {
    let btns_change_month = document.querySelectorAll('.change-month');

    btns_change_month.forEach(btn => {
        btn.addEventListener('click', (e) => {
            let url = "/get-month?";
            params = {
                year: document.querySelector('#inp-year').value, 
                month: document.querySelector('#inp-month').value
            }
    
            for (let key in params) {
                url += key + '=' + params[key] + '&';
            }
    
            fetch(url)
            .then(response => response.json())
            .then(result => {

                if (e.target.id == "next-month-btn") {
                    document.querySelector('#inp-year').value = result.next_year;
                    document.querySelector('#inp-month').value = result.next_month;
                    window.location.href = `?year=${result.next_year}&month=${result.next_month}`;
                } else {
                    document.querySelector('#inp-year').value = result.last_year;
                    document.querySelector('#inp-month').value = result.last_month;
                    window.location.href = `?year=${result.last_year}&month=${result.last_month}`;
                }
            })
        });
    });
}

function editEvent(csrftoken) {
    all_events = document.querySelectorAll('.event');
    all_events.forEach(event => {
        event.addEventListener('click', () => {
            let event_description = event.querySelector('.event-description').innerHTML;
            let times = event.querySelector('.times').innerHTML.split(' - ');
            document.querySelector('[data-bs-target="#addDayModal"]').click();
            document.querySelector('#description').innerHTML = event_description;

            if (times[0].length == 4) {
                times[0] = '0' + times[0];
            }
            if (times[1].length == 4) {
                times[1] = '0' + times[1];
            }

            document.getElementById('time-event').value = times[0];
            document.getElementById('time-event_to').value = times[1];
            document.getElementById('event-id').value = event.getAttribute('id');
            console.log(event.querySelector('.repeat-inp').checked);

            if (event.querySelector('.repeat-inp').checked) {
                document.querySelector('#repeat').checked = true;
            }

            document.querySelector('#addDayModalLabel').innerHTML = 'Редактировать событие';
            document.querySelector('[form="add-event-form"]').innerHTML = 'Редактировать';

            let deleteBtn = document.createElement('button');

            if(!document.querySelector('.btn-danger')) {
                deleteBtn.className = 'btn btn-danger';
                deleteBtn.innerHTML = 'Удалить';
                document.querySelector('.modal-footer').append(deleteBtn);
            }

            deleteBtn.addEventListener('click', () => {
                console.log('Delete!');
                fetch('/delete-event', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify({
                        event_id: event.getAttribute('id'),
                        year: document.querySelector('[name="year"]').value,
                        month: document.querySelector('[name="month"]').value,
                        day: document.querySelector('[name="day"]').value,
                    })
                  })
                  .then(response => response.json())
                  .then(result => {
                    console.log(result.event_id);
                    data_attr = "[id='" + result.event_id + "']";
                    document.querySelector(data_attr).remove();
                    document.querySelector('[data-bs-dismiss="modal"]').click();
                  });  
            });
        });
    });
}

function change_followers(csrftoken) {
    allChangeFollowersBtn = document.querySelectorAll('.change-approve');
    allChangeFollowersBtn.forEach(elBtn => {
        elBtn.addEventListener('click', (e) => {
            let userId = elBtn.parentNode.getAttribute('id');
            fetch(`/change-follower/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
              })
              .then(response => response.json())
              .then(result => {
                console.log(result);
                if (result.is_approved) {
                    elBtn.remove();
                } else {
                    elBtn.innerHTML = '+';
                    elBtn.className = 'btn btn-primary change-approv';
                }
            });  
        });
    });
}

function search() {
    let search_btn = document.querySelector('#search-button');
    search_btn.addEventListener('click', () => {
        let input_search = document.querySelector('[type="search"]').value;
        fetch(`/search_input?username=${input_search}`)
        .then(response => response.json())
        .then(result => {
            if (!result.error) {
                window.location.href = `/profile/${result.user_id}`;
            } else {
                console.log(result.error);
            }
        })
    });
}

function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const observer = new MutationObserver((mutations, obs) => {
            const element = document.querySelector(selector);
            if (element) {
                obs.disconnect();
                resolve(element);
            }
        });

        observer.observe(document, {
            childList: true,
            subtree: true,
        });

        setTimeout(() => {
            observer.disconnect();
            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
        }, timeout);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function delete_follower(csrftoken) {
    let btns_delete_followers = document.querySelectorAll('.delete-follower');

    btns_delete_followers.forEach(delete_btn => {
        delete_btn.addEventListener('click', () => {
            user_id = delete_btn.parentNode.id;
            fetch('/delete_follower', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    user_id: user_id,
                })
              })
            .then(response => response.json())
            .then(result => {
                if (!result.error) {
                    document.getElementById(user_id).remove();
                }
            })
        });
    });
}