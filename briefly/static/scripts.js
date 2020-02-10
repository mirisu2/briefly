function makeUL(array) {
    let list = document.createElement('ul');
    list.setAttribute('class', 'custom-ul')
    for (let i = 0; i < array.length; i++) {
        let item = document.createElement('li');

        let item_a = document.createElement('a');
        item_a.setAttribute('href', array[i]['author_url']);
        item_a.setAttribute('target', '_blank');
        item_a.appendChild(document.createTextNode(array[i]['author_fullname']));
        item.appendChild(item_a);

        list.appendChild(item);
    }
    return list;
}

function selectLetter(evt, letter) {
    letters = document.getElementsByClassName("letter");
    for (i = 0; i < letters.length; i++) {
        letters[i].className = letters[i].className.replace(" active", "");
    }
    evt.currentTarget.className += " active";

    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(this.responseText);
            if (data['status'] == true) {
                document.getElementById("author_number").innerHTML = 'Found records: ' + data['number_of_records'];
                document.getElementById("authors-list").innerHTML = ''
                document.getElementById("authors-list").appendChild(makeUL(data['authors']));
            }
        }
    };
    xhttp.open("GET", "/authors/" + letter, true);
    xhttp.send();
}

