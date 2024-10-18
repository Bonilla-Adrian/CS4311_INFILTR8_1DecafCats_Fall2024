<!--TODO: Add current project file?? -->
<!--TODO: Add ability to select multiple rows -->
<!--TODO: Visual improvements DONE BY ASHLEY RIVAS-->
<!--TODO: add Logging of Export request to the User Actions -->

<script>
	import { onMount } from 'svelte';
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Button,
		Dropdown,
		DropdownItem,
		Checkbox,
		ButtonGroup
	} from 'flowbite-svelte';
	import { Heading, P, Mark } from 'flowbite-svelte';

	let theme = 'light'; // Default theme

	onMount(() => {
		console.log('Report component mounted');
	});

	// Function to toggle theme
	function toggleTheme() {
		theme = theme === 'light' ? 'dark' : 'light';
		document.body.setAttribute('data-theme', theme);
		localStorage.setItem('theme', theme); // Save theme preference
	}

	let selectedFile;

	const handleFileChange = (event) => {
		selectedFile = event.target.files[0];
	};

	let data = [];
	const headers = new Headers();
	headers.append('Content-Type', 'application/json');
	// Fetch data to mimic fetching a file
	async function testGet() {
		try {
			const response = await fetch('http://127.0.0.1:5000/flask-api/test2', {method: 'GET',});
			if (!response.ok) {
				const errorText = await response.text();
				throw new Error('Failed to fetch data');
			}
			const jsonData = await response.json();
			data = jsonData; // Ensure jsonData is actually an array if this assignment is made
			console.log(data);
		} catch (err) {
			console.log('Error fetching data:',err);
		}
	}

	async function sendFile(file) {
		const formData = new FormData()
		formData.append('file', file)
		console.log(formData)
		const response = await fetch("/flask-api/nessus-upload", {
			method: 'POST',
			body: formData
		});
		const jsonData = await response.json();
		data = jsonData; // Ensure jsonData is actually an array if this assignment is made
		console.log(data);
	}

	function handleDataBaseTest() {
		testGet();
		sendFile(selectedFile);
	}

	let rows = [
		{
			id: 1,
			ipAddress: '38.241.13.107',
			device: 'Device 1',
			vulnerability: 'CVE-2024-0101 (SQL Injection in User Authentication)',
			status: 'Exploited',
			selected: false
		},
		{
			id: 2,
			ipAddress: '49.6.148.87',
			device: 'Device 2',
			vulnerability: 'CVE-2024-3033 (Buffer Overflow in File Upload Handler)',
			status: 'Exploited',
			selected: false
		},
		{
			id: 3,
			ipAddress: '22.146.141.10',
			device: 'Device 12',
			vulnerability: 'CVE-2024-2022 (Cross-Site Scripting in Profile Management)',
			status: 'Not Exploited',
			selected: false
		},
		{
			id: 4,
			ipAddress: '11.27.177.103',
			device: 'Device 462',
			vulnerability: 'CVE-2024-6066 (Remote Code Execution in API Endpoint)',
			status: 'Exploited',
			selected: false
		}
	];

	let exportFormat = 'Format to export';
	let selectAll = true ;

	// Toggle individual row selection
	//function toggleSelect(row) {
	//	row.selected = !row.selected;
	//}
	//function toggleSelect(row) {
  	//	if (row.selected !== selectAll) {
    //		row.selected = !row.selected;
  	//	}
	//}

	// Toggle "Select All" functionality
	//function toggleSelectAll() {
	//	selectAll = !selectAll;
	//	rows.forEach((row) => row.selected = selectAll);
	//}

	//function toggleSelectAll() {
  	//	selectAll = !selectAll;
  	//	rows.forEach((row) => {
    //		row.selected = selectAll ? !row.selected : row.selected;
  	//	});

	//	this.$set({ selectAll });
	//}


	// Toggle "Select All" functionality
	function toggleSelectAll() {
		selectAll = !selectAll;
		rows = rows.map(row => ({
			...row,
			selected: selectAll
		}));
	}

	// Toggle individual row selection and update "Select All" checkbox if needed
	function toggleSelect(row) {
		row.selected = !row.selected;
		// Check if all rows are selected after toggling
		selectAll = rows.every(row => row.selected);
	}
	function handleExportFormatChange(event) {
		exportFormat = event.target.value;
	}

	function handleExport() {
		if (exportFormat === 'Format to export') {
			alert('Please select a format to export.');
			return;
		}

		// Log the export request and the selected rows
		const selectedRows = rows.filter((row) => row.selected);
		console.log('Export Request:', exportFormat, selectedRows);

		// Simulate export process (you can replace this with actual logic)
		alert(`Exporting ${selectedRows.length} rows in ${exportFormat}`);
		// Redirect or handle export logic here
	}

	onMount(() => {
		// Call testGet when component mounts
		handleDataBaseTest();
		theme = localStorage.getItem('theme') || 'light';
		document.body.setAttribute('data-theme', theme);
	});
</script>

<!-- Main report container -->
<div class="report-container dark:bg-gray-800">
	<Heading
		tag="h1"
		class="gradient heading mb-4 text-center text-3xl font-extrabold md:text-5xl lg:text-6xl"
	>
		REPORTS
	</Heading>

	<!-- Data Table -->
	<Table class="shadow-md sm:rounded-lg">
		<TableHead>
			<TableHeadCell padding="px-4 py-3">
				<!-- Select All Checkbox -->
				<input 
					type="checkbox" 
					checked={selectAll} 
					on:change={toggleSelectAll} 
				/>
			</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">IP Address</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Device</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Vulnerability</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Status</TableHeadCell>
		</TableHead>

		<TableBody class="divide-y">
			{#each rows as row (row.id)}
				<TableBodyRow>
					<TableBodyCell>
						<!-- Individual Row Checkbox -->
						<input
							type="checkbox"
							checked={row.selected}
							on:change={() => toggleSelect(row)}
						/>
					</TableBodyCell>
					<TableBodyCell>{row.ipAddress}</TableBodyCell>
					<TableBodyCell>{row.device}</TableBodyCell>
					<TableBodyCell>{row.vulnerability}</TableBodyCell>
					<TableBodyCell>{row.status}</TableBodyCell>
				</TableBodyRow>
			{/each}
		</TableBody>
	</Table>

	<!-- Dropdown for export format -->
	<div class="dropdown-container">
		<Dropdown label="Export Format">
			<DropdownItem on:click={() => handleExportFormatChange({ target: { value: 'word' } })}>
				Word Document (.docx)
			</DropdownItem>
			<DropdownItem on:click={() => handleExportFormatChange({ target: { value: 'pdf' } })}>
				PDF Document (.pdf)
			</DropdownItem>
		</Dropdown>
	</div>

	<!-- Export button -->
	<div class="export-button-container">
		<button class="export-button" on:click={handleExport}> Export </button>
	</div>

	<!-- Database test button -->
	<div class="database-container">
		<button class="test-button" on:click={handleDataBaseTest}> Database Test </button>
	</div>

	<div>
		<input type="file" on:change="{handleFileChange}" />
	</div>
</div>

<style>
	:root {
		--bg-color: #ffffff; /* Light background color */
		--text-color: #000000; /* Light text color */
		--button-bg: blue; /* Light button background color */
		--button-text: white; /* Light button text color */
		--table-header-bg: #f2f2f2; /* Light table header background */
		--table-padding-bg: #ffffff; /* Light background color for table padding */
	}

	.report-container {
		display: flex;
		flex-direction: column;
		align-items: center; /* Center items horizontally */
		justify-content: flex-start; /* Align items to the start vertically */
		width: 100%; /* Full width */
		max-width: 1200px; /* Maximum width to ensure container does not get too wide */
		margin: 0 auto; /* Center the container horizontally */
		padding: 20px; /* Padding inside the container */
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Optional: Adds shadow for better visibility */
		border-radius: 10px; /* Optional: Rounds the corners */
	}

	/* Responsive adjustments for smaller screens */
	@media (max-width: 768px) {
		.report-container {
			padding: 10px;
			flex-direction: column;
		}
	}

	.dropdown-container,
	.export-button-container,
	.database-container {
		margin-top: 20px;
	}

	.export-button,
	.test-button {
		padding: 10px 20px;
		font-size: 16px;
		cursor: pointer;
		border: none;
		border-radius: 4px;
		background-color: var(--button-bg);
		color: var(--button-text);
	}
</style>
