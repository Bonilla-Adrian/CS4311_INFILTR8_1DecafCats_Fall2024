<script>
    import { SystemInfo } from '../../lib/SystemInfo.js';
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import { Chart, Card, A, Button, Dropdown, DropdownItem, Popover, Tooltip, Progressbar } from 'flowbite-svelte';
    import { InfoCircleSolid, ArrowDownToBracketOutline, ChevronDownOutline, ChevronRightOutline, PenSolid, DownloadSolid, ShareNodesSolid, ShareNodesOutline } from 'flowbite-svelte-icons';
    import { onMount, onDestroy } from 'svelte';

    let tableData = [];
    let series = [0, 0, 0]; 
    let latestProject = null;
    let username = "";
    
    async function checkSession(){
        try{
            const response = await fetch('/flask-api/check_session',{
                method: 'GET',
                credentials: 'include'
            });
            if (response.ok){
                const sessionData = await response.json();
                if (sessionData.logged_in){
                    username = sessionData.username;
                }else{
                    console.error("User is not logged in");
                }
            } else{
                console.error("Failed to fetch session data");
            }

        }catch (error){
            console.error("Error checking session:", error);
        }
    }

    onMount(() => {
        const initialize = async () => {
            await checkSession();
            setInterval(async () => {
                await getTableData();
            }, 500);
        }
        initialize();
    });


    async function logButtonClick(detail) {
        console.log("Button clicked with detail:", detail);  // For debugging
        try {
            const response = await fetch('/flask-api/log-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username || 'Anonymous',  // Dummy username for now
                    action: 'ButtonClick',
                    details: detail
                })
            });

            if (!response.ok) {
                throw new Error('Failed to log action');
            }

            const result = await response.json();
            console.log('Action logged:', result);
        } catch (error) {
            console.error('Failed to log button click:', error);
        }
    }

    async function downloadLogs() {
        const date = getFormattedDate(); 
        try {
            const response = await fetch(`/flask-api/download-logs/${date}`);
            if (!response.ok) {
                throw new Error('Failed to download logs');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `logs_${date}.log`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (error) {
            console.error('Failed to download logs:', error);
        }
    }

    async function getTableData(){
        try {
            const response = await fetch("/flask-api/get-all-project-info", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();
            tableData = Object.values(data).flatMap(Object.values);
            tableData = tableData.filter(row => row.status != null);
            series = [0, 0, 0];
            tableData.forEach(row => {
                if (row.status === 'reports') {
                    series[2]++;
                } else if (row.status === 'scheduled') {
                    series[1]++;
                } else {
                    series[0]++;
                }
            });

            // Get the latest project by date
            if (tableData.length > 0) {
                latestProject = tableData.reduce((latest, current) => 
                    new Date(current.creation) > new Date(latest.creation) ? current : latest
                );
            }

        } catch (error) {
            console.error("There was an error retrieving data from the backend:", error);
        }
    }


    function getFormattedDate() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const sysInfo = new SystemInfo()
    var timestamp = sysInfo.getCurrentTimestamp()
    var date =  sysInfo.getFormattedDate()

</script>

<main>
    
    <h1 class="font-bold text-xl dark:text-white">Analysis</h1>

    <div>
        <!-- start of the left column -->   
          
        <div id="left" class="float-left  w-8/12 h-flex   ">
            <!-- table section -->
            <div id="table" class="my-6">
                <Table noborder={true}>
                    <TableHead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-900 dark:text-gray-400 ">
                        <TableHeadCell>Date</TableHeadCell>
                        <TableHeadCell>Analyst</TableHeadCell>
                        <TableHeadCell>File Size</TableHeadCell>
                        <TableHeadCell>Progress</TableHeadCell>
                    </TableHead>
                    <TableBody>
                        {#if tableData.length > 0}
                            {#each tableData as row}
                                <TableBodyRow>
                                    <TableBodyCell>{row.creation}</TableBodyCell>
                                    <TableBodyCell>{row.user}</TableBodyCell>
                                    <TableBodyCell>{row.fileSize}</TableBodyCell>
                                    <TableBodyCell>
                                        {#if typeof row.status === 'number'}
                                            <Progressbar progress={row.status} labelInside />
                                        {:else}
                                            <button class="border-2 py-2 px-2 shadow-lg rounded-2xl self-center">{row.status}</button>
                                        {/if}
                                    </TableBodyCell>
                                </TableBodyRow>
                            {/each}
                        {:else}
                            <TableBodyRow>
                                <TableBodyCell colspan="4" class="text-center">
                                    No existing projects
                                </TableBodyCell>
                            </TableBodyRow>
                        {/if}
                    </TableBody>
                </Table>
            </div>
        </div>

        <!-- start of the right column  and Anaysis Progress-->
        <div id="right" class="flex-top float-right  w-3/12 h-dvh mr-20 py-6">
            <!-- start of the pie chart -->
            <div id="topChart">
                <Card>
                    <h5 class="text-xl font-bold leading-none text-gray-900 dark:text-gray-400 mb-2">Analysis Progress</h5>
                    <Chart
                        options={{
                            chart: { type: 'donut', height: 280, width: '100%' },
                            series: series,
                            colors: ['#1C64F2', '#16BDCA', '#FDBA8C'],
                            stroke: { colors: ['transparent'], lineCap: '' },
                            plotOptions: {
                                pie: {
                                    donut: {
                                        labels: {
                                            show: true,
                                            name: { show: true, fontFamily: 'Inter, sans-serif', offsetY: 20 },
                                            total: {
                                                showAlways: true,
                                                show: true,
                                                label: 'Projects',
                                                fontFamily: 'Inter, sans-serif',
                                                formatter: (w) => w.globals.seriesTotals.reduce((a, b) => a + b, 0)
                                            },
                                            value: { show: true, fontFamily: 'Inter, sans-serif', offsetY: -20 }
                                        },
                                        size: '80%'
                                    }
                                }
                            },
                            labels: [
                                '<span class="text-analyzing dark:text-white">Analyzing</span>',
                                '<span class="text-scheduled dark:text-white">Scheduled</span>',
                                '<span class="text-completed dark:text-white">Completed</span>'
                            ],
                            legend: { position: 'bottom', fontFamily: 'Inter, sans-serif' },
                            dataLabels: { enabled: false },
                            grid: { padding: { top: -2 } }
                        }}
                        class="py-6"
                    />
                </Card>
            </div>
            
            <!-- start of current project settings -->
            <div id="bottomSettings" class=" py-6 rounded-md shadow-2xl  ">
                <h2 class="text-center font-bold leading-none text-gray-900 dark:text-gray-400  me-1 dark:bg-gray-900">Current Test</h2>
            
                {#if latestProject}
                    <div class="px-2 dark:text-white dark:bg-gray-700">
                        <p>Project Name: {latestProject.projectName}</p>
                        <p>Analyst: {latestProject.user}</p>
                        <p>File Size: {latestProject.fileSize}</p>
                        <p>Status: {latestProject.status}</p>
                        <p>Time Started: {latestProject.creation}</p>
                        <button 
                            on:click={() => logButtonClick('Dummy button clicked')}
                            on:click={downloadLogs} 
                            class="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"                            >
                            Download Logs
                        </button>
                    </div>
                {:else}
                    <p class="text-center">No current test available.</p>
                {/if}
            
            </div>

            <!-- Entry Points dropdown section
            <div id="entryPoints" class="my-6 ">
                <label for="entry-point-type" class=" dark:text-white block text-sm font-medium text-gray-700">Entry Points</label>
                <select id="entry-point-type" name="entry-point-type" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                    <option value="" selected>All</option>
                    <option value="unauthorized-port-bypass">Unauthorized Port Bypass</option>
                    <option value="default-credentials">Default Credentials</option>
                    <option value="unpatched-software">Unpatched Software Exploits</option>
                    <option value="protocols-missing-encryption">Protocols Missing Encryption</option>
                    <option value="weak-passwords">Weak Passwords</option>
                </select>
            </div>
            <div id="viewResults" class="my-6">
                <button type="button" class="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
                    View Results
                </button>
            </div> -->

        </div>
        <div id="middle" class="flex-top float-left  w-8/12  py-0">
            <!-- start of Summary-->
            <div id="bottomSettings" class="py-8 shadow-2xl dark:bg-gray-900">
                <h2 class="flex justify-center items-center text-center font-bold text-xl leading-none text-gray-900 dark:text-white me-1 dark:bg-gray-900">
                    <span class="flex-1 text-center">Summary</span>
                    <button Dropdown button ChevronDownOutline class="p-0 bg-transparent border-none cursor-pointer outline-none ml-auto" aria-label="Filter Icon">
                      <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                        <path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M18.796 4H5.204a1 1 0 0 0-.753 1.659l5.302 6.058a1 1 0 0 1 .247.659v4.874a.5.5 0 0 0 .2.4l3 2.25a.5.5 0 0 0 .8-.4v-7.124a1 1 0 0 1 .247-.659l5.302-6.059c.566-.646.106-1.658-.753-1.658Z"/>

                      </svg>
                    </button>
                    <Dropdown>
                        <DropdownItem>Low Vulnerability</DropdownItem>
                        <DropdownItem>Mid Vulnerability</DropdownItem>
                        <DropdownItem>High Vulnerability</DropdownItem>
                        <DropdownItem></DropdownItem>
                      </Dropdown>
                      
                  </h2>
                  
                  
                
                  
                <div class="overflow-y-auto h-11  max-w-2xs lg:h-[calc(100vh-30rem)] lg:block dark:bg-gray-800 lg:me-0 lg:sticky top-2 px-2 dark:text-white">
                    <p>Current Testing</p>
                    <p>Weak password Attack</p>
                    <p>Device X</p>
                    <p>IP 17.172.224.47</p>
                    <p>Device C</p>
                    <p>Status OK/</p>
                    <p>------ {timestamp}-------</p>
                    <p> &nbsp;</p>

                    <p>Current Testing</p>
                    <p>Weak password Attack</p>
                    <p>Device X</p>
                    <p>IP 17.172.224.46</p>
                    <p>Device C</p>
                    <p>Status OK/</p>
                    <p></p>
                    <p>------ {timestamp}-------</p>
                    <p> &nbsp;</p>

                    <p>Current Testing</p>
                    <p>Weak password Attack</p>
                    <p>Device X</p>
                    <p>IP 17.172.224.48</p>
                    <p>Device C</p>
                    <p>Status OK/</p>
                    <p></p>
                    <p>------ {timestamp}-------</p>
                    <p> &nbsp;</p>

                    <p>Current Testing</p>
                    <p>Weak password Attack</p>
                    <p>Device Z</p>
                    <p>IP 17.172.224.4</p>
                    <p>Device C</p>
                    <p>Status OK/</p>
                    <p>------ {timestamp}-------</p>
                    <p> &nbsp;</p>
                    


                    <p> {timestamp}</p>
                    
                </div>
            </div>
        </div>
        
            
    </div>
     
    
</main>