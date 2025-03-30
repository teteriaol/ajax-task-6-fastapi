async function fetchJobPositions() {
    let response = await axios.get('/positions');
    let jobPositions = response.data;
    let positionsTableBody = document.querySelector('.positions-table tbody');
    let fromPositionDropdown = document.querySelector('.from-position');
    let toPositionDropdown = document.querySelector('.to-position');

    positionsTableBody.innerHTML = '';
    fromPositionDropdown.innerHTML = '';
    toPositionDropdown.innerHTML = '';

    jobPositions.forEach(position => {
        let newRow = positionsTableBody.insertRow();
        let dropdownOption = document.createElement('option');

        newRow.innerHTML = `<td>${position.name}</td><td><button onclick="removeJobPosition('${position.name}')">Delete</button></td>`;
        dropdownOption.value = position.name;
        dropdownOption.textContent = position.name;
        fromPositionDropdown.appendChild(dropdownOption.cloneNode(true));
        toPositionDropdown.appendChild(dropdownOption);
    });
}

async function createJobPosition() {
    let positionNameInput = document.querySelector('.position-name').value;
    if (!positionNameInput) {
        return;
    }

    await axios.post('/positions', { name: positionNameInput });
    fetchJobPositions();
    document.querySelector('.position-name').value = '';
}

function removeJobPosition(positionName) {
    axios.delete('/positions/' + positionName).then(fetchJobPositions);
}

function createPositionDependency() {
    let fromPosition = document.querySelector('.from-position').value;
    let fromLevel = document.querySelector('.from-level').value;
    let toPosition = document.querySelector('.to-position').value;
    let toLevel = document.querySelector('.to-level').value;
    let salaryFormula = document.querySelector('.formula-salary').value;
    let bonusFormula = document.querySelector('.formula-bonus').value;
 
    let dependencyDetails = {
        from_position: fromPosition,
        from_level: fromLevel,
        to_position: toPosition,
        to_level: toLevel,
        formula_salary: salaryFormula,
        formula_bonus: bonusFormula
    };
    
    axios.post('/dependencies', dependencyDetails).then(function() {
        document.querySelectorAll('input, select').forEach(function(element) {
            element.value = '';
        });
        fetchJobPositions();
        updateResultsTable();
    });
}

function showSalaryResults(results) {
    let resultsContainer = document.querySelector('.results-table');
    resultsContainer.innerHTML = '';
    
    if (!results) return;
    
    let tableHtml = '<table><thead><tr><th>Position</th>';
    for (let level = 1; level <= 4; level++) {
        tableHtml += `<th>ЗП${level}</th><th>Бонус${level}</th><th>Сума${level}</th>`;
    }
    
    tableHtml += '</tr></thead><tbody>';
    for (let positionName in results) {
        if (results.hasOwnProperty(positionName)) {
            tableHtml += `<tr><td>${positionName}</td>`;
            let positionLevels = results[positionName].levels || [];
            
            for (let idx = 0; idx < 4; idx++) {
                let levelData = positionLevels[idx] || {};
                tableHtml += `
                    <td>${(levelData.base_salary || 0).toFixed(2)}</td>
                    <td>${(levelData.bonus || 0).toFixed(2)}</td>
                    <td>${(levelData.total || 0).toFixed(2)}</td>
                `;
            }
            
            tableHtml += '</tr>';
        }
    }
    
    tableHtml += '</tbody></table>';
    resultsContainer.innerHTML = tableHtml;
}

async function updateResultsTable() {
    axios.get('/calculate').then(function(response) {
        showSalaryResults(response.data && response.data.results);
    });
}