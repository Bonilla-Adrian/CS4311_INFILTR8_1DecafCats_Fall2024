<!--TODO: Add current project file?? -->
<!--TODO: Add ability to select multiple rows -->
<!--TODO: Visual improvements DONE BY ASHLEY RIVAS-->
<!--TODO: add Logging of Export request to the User Actions -->

<script>
	import { onMount } from 'svelte';
	import Papa from 'papaparse';
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Dropdown,
		DropdownItem,
	} from 'flowbite-svelte';
	import { Heading } from 'flowbite-svelte';

	let theme = 'light';
	let rows = [];
	let selectAll = true;
	let exportFormat = 'Format to export';

	// Fetch and parse the CSV file from the backend
	async function fetchCSV() {
		try {
			const response = await fetch('../../../backend/output/ranked_entry_points.csv');
			if (!response.ok) throw new Error('Failed to fetch CSV file');
			const csvText = await response.text();

			// Parse CSV data using PapaParse
			Papa.parse(csvText, {
				header: true,
				skipEmptyLines: true,
				complete: (results) => {
					// Log parsed data to inspect its structure
					console.log('Parsed CSV Data:', results.data);

					// Map parsed data to rows format based on new headers
					rows = results.data.map((row, index) => ({
						id: index + 1,
						ip: row['ip'] || '',
						port: row['port'] || '',
						severity_score: row['severity_score'] || '',
						exploit_score: row['exploit_score'] || '',
						distinct_vulnerabilities: row['distinct_vulnerabilities'] || '',
						combined_score: row['combined_score'] || '',
						selected: false
					}));
				}
			});
		} catch (error) {
			console.error('Error fetching and parsing CSV:', error);
		}
	}

	onMount(() => {
		console.log('Report component mounted');
		theme = localStorage.getItem('theme') || 'light';
		document.body.setAttribute('data-theme', theme);
		fetchCSV(); // Fetch the CSV data on mount
	});

	function toggleTheme() {
		theme = theme === 'light' ? 'dark' : 'light';
		document.body.setAttribute('data-theme', theme);
		localStorage.setItem('theme', theme);
	}

	function toggleSelectAll() {
		selectAll = !selectAll;
		rows = rows.map((row) => ({ ...row, selected: selectAll }));
	}

	function toggleSelect(row) {
		row.selected = !row.selected;
		selectAll = rows.every((row) => row.selected);
	}

	function handleExportFormatChange(event) {
		exportFormat = event.target.value;
	}

	async function handleExport() {
		if (exportFormat === 'Format to export') {
			alert('Please select a format to export.');
			return;
		}

		const selectedRows = rows.filter((row) => row.selected);
		const selectedIPs = selectedRows.map(row => row.ip);

		console.log('Export Request:', exportFormat, selectedRows);

		try {
			const response = await fetch("http://127.0.0.1:5000/flask-api/log_export", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ ip_addresses: selectedIPs, export_format: exportFormat })
			});

			if (response.ok) {
				console.log("Export logged successfully");
			} else {
				console.error("Failed to log export");
			}
		} catch (error) {
			console.error("Error logging export:", error);
		}

		alert(`Exporting ${selectedRows.length} rows in ${exportFormat}`);
	}
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
	<Table class="shadow-md sm:rounded-lg mt-4">
		<TableHead>
			<TableHeadCell padding="px-4 py-3">
				<input type="checkbox" checked={selectAll} on:change={toggleSelectAll} />
			</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">IP</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Port</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Severity Score</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Exploit Score</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Distinct Vulnerabilities</TableHeadCell>
			<TableHeadCell padding="px-4 py-3">Combined Score</TableHeadCell>
		</TableHead>

		<TableBody class="divide-y">
			{#each rows as row (row.id)}
				<TableBodyRow>
					<TableBodyCell>
						<input type="checkbox" checked={row.selected} on:change={() => toggleSelect(row)} />
					</TableBodyCell>
					<TableBodyCell>{row.ip}</TableBodyCell>
					<TableBodyCell>{row.port}</TableBodyCell>
					<TableBodyCell>{row.severity_score}</TableBodyCell>
					<TableBodyCell>{row.exploit_score}</TableBodyCell>
					<TableBodyCell>{row.distinct_vulnerabilities}</TableBodyCell>
					<TableBodyCell>{row.combined_score}</TableBodyCell>
				</TableBodyRow>
			{/each}
		</TableBody>
	</Table>

	<!-- Dropdown for export format -->
	<div class="dropdown-container mt-4">
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
	<div class="export-button-container mt-4">
		<button class="export-button" on:click={handleExport}> Export </button>
	</div>
</div>

<style>
	:root {
		--bg-color: #ffffff;
		--text-color: #000000;
		--button-bg: blue;
		--button-text: white;
		--table-header-bg: #f2f2f2;
		--table-padding-bg: #ffffff;
	}

	.report-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-start;
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
		border-radius: 10px;
	}

	.dropdown-container,
	.export-button-container {
		margin-top: 20px;
	}

	.export-button {
		padding: 10px 20px;
		font-size: 16px;
		cursor: pointer;
		border: none;
		border-radius: 4px;
		background-color: var(--button-bg);
		color: var(--button-text);
	}
</style>
