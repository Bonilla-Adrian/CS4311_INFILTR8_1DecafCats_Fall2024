<script>
    import { SystemInfo } from '../../lib/SystemInfo.js'
    import  { Progressbar } from 'flowbite-svelte';
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import { Chart, Card, A, Button, Dropdown, DropdownItem, Popover, Tooltip } from 'flowbite-svelte';
    import { InfoCircleSolid, ArrowDownToBracketOutline, ChevronDownOutline, ChevronRightOutline, PenSolid, DownloadSolid, ShareNodesSolid } from 'flowbite-svelte-icons';
    import { onMount } from 'svelte';
    import { session, checkSession } from '$lib/stores/session.js';

    onMount(() => {
        checkSession(); // Check session on page load
    });

    // pie chart
    const options = {
        series: [1, 1, 3],
        colors: ['#1C64F2', '#16BDCA', '#FDBA8C'],
        chart: {height: 280,width: '100%',type: 'donut'},
        stroke: {colors: ['transparent'],lineCap: ''},
        plotOptions: {
        pie: {
            donut: {
            labels: {
                show: true,
                name: {
                show: true,
                fontFamily: 'Inter, sans-serif',
                offsetY: 20
                },
                total: {
                showAlways: true,
                show: true,
                label: 'Projects',
                fontFamily: 'Inter, sans-serif',
                formatter: function (w) {
                    const sum = w.globals.seriesTotals.reduce((a, b) => {
                    return a + b;
                    }, 0);
                    return `${sum}`;
                }
                },
                value: {
                show: true,
                fontFamily: 'Inter, sans-serif',
                offsetY: -20,
                formatter: function (value) {
                    return value + 'k';
                }
                }
            },
            size: '80%'
            }
        }
        },
        grid: {padding: {top: -2}},
        labels: [
        '<span class="text-analyzing dark:text-white ">Analyzing</span>',
        '<span class="text-scheduled dark:text-white">Scheduled</span>',
        '<span class="text-completed dark:text-white">Completed</span>',
    ],
        dataLabels: {enabled: false},
        legend: {position: 'bottom', fontFamily: 'Inter, sans-serif dark:text-white'},
        yaxis: {
        labels: {
            formatter: function (value) {
            return value + 'k';
            }
        }
        },
        xaxis: {
        labels: {
            formatter: function (value) {
            return value + 'k';
            }
        },
        axisTicks: {
            show: false
        },
        axisBorder: {
            show: false
        }
        }
    };

    const sysInfo = new SystemInfo()
    var timestamp = sysInfo.getCurrentTimestamp()
    var date =  sysInfo.getFormattedDate()


    async function logButtonClick(detail) {
        console.log("Button clicked with detail:", detail);  // For debugging
        try {
            const response = await fetch('/flask-api/log-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: 'DummyUser',  // Dummy username for now
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
        const date = new Date().toISOString().slice(0, 10);  // Get today's date in 'YYYY-MM-DD' format
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
            a.download = `logs_${date}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (error) {
            console.error('Failed to download logs:', error);
        }
    }
   
</script>




<!-- whole page -->
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
                    <TableBodyRow class=" " on:click>
                        <TableBodyCell>9/13/2024 - 10:00:00 AM</TableBodyCell>
                        <TableBodyCell>John Doe</TableBodyCell>
                        <TableBodyCell>--</TableBodyCell>
                        <TableBodyCell><button class="border-2 shadow-gray-400 py-2 px-2 shadow-lg rounded-2xl self-center">Scheduled</button></TableBodyCell>
                    </TableBodyRow>
                    <TableBodyRow>
                        <TableBodyCell>9/12/2024 - 10:00:00 AM</TableBodyCell>
                        <TableBodyCell>John Doe</TableBodyCell>
                        <TableBodyCell>2.1 mb</TableBodyCell>
                        <TableBodyCell><Progressbar progress="43" labelInside /></TableBodyCell>
                    </TableBodyRow>
                    <TableBodyRow>
                        <TableBodyCell>9/10/2024 - 10:43:21 AM</TableBodyCell>
                        <TableBodyCell>John Doe</TableBodyCell>
                        <TableBodyCell>3.2 mb</TableBodyCell>
                        <TableBodyCell><button class="border-2 py-2 px-2 shadow-lg rounded-2xl self-center">Reports</button></TableBodyCell>
                    </TableBodyRow>
                    <TableBodyRow>
                        <TableBodyCell>9/09/2024 - 10:05:21 AM</TableBodyCell>
                        <TableBodyCell>John Doe</TableBodyCell>
                        <TableBodyCell>3.2 mb</TableBodyCell>
                        <TableBodyCell><button class="border-2 py-2 px-2 shadow-lg rounded-2xl self-center">Reports</button></TableBodyCell>
                    </TableBodyRow>
                    <TableBodyRow>
                        <TableBodyCell>9/07/2024 - 9:43:21 AM</TableBodyCell>
                        <TableBodyCell>John Doe</TableBodyCell>
                        <TableBodyCell>3.2 mb</TableBodyCell>
                        <TableBodyCell><button class="border-2 py-2 px-2 shadow-lg rounded-2xl self-center">Reports</button></TableBodyCell>
                    </TableBodyRow>
                    </TableBody>
                </Table>
              </div>    
        </div>

        <!-- start of the right column  and Anaysis Progress-->
        <div id="right" class="flex-top float-right  w-3/12 h-dvh mr-20 py-6">
            <!-- start of the pie chart -->
            <div id="topChart">
                <Card>
                    <div class="flex justify-between items-start w-full">
                      <div class="flex-col items-center">
                        <div class="flex items-center mb-1">
                          <h5 class="text-xl font-bold leading-none text-gray-900 dark:text-gray-400 me-1">Analysis progress</h5>
                          <InfoCircleSolid id="donut1" class="w-3.5 h-3.5 text-gray-500 dark:text-white hover:text-gray-900 dark:hover:text-white cursor-pointer ms-1" />
                          <Popover triggeredBy="#donut1" class="text-sm text-gray-500 bg-white border border-gray-200 rounded-lg shadow-sm w-72 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 z-10">
                            <div class="p-3 space-y-2">
                              <h3 class="font-semibold te dark:text-white">Progress Chart</h3>
                              <p>Shows the amount of projects that are completed, scheduled and are currently being analyzed</p>
                            </div>
                          </Popover>
                        </div>
                      </div>
                    </div> 
                    <Chart {options} class="py-6" />
                  </Card>
            </div>
            
            <!-- start of current project settings -->
            <div id="bottomSettings" class=" py-6 rounded-md shadow-2xl  ">
                <h2 class="text-center font-bold  font-bold leading-none text-gray-900 dark:text-gray-400  me-1 dark:bg-gray-900">Current Test</h2>
                
                <div class="px-2 dark:text-white dark:bg-gray-700">
                    <p>Project Name: Test Run</p>
                    <p>Analyst: John Doe</p>
                    <p>File Location: /Path/goes/here/</p>
                    <p>Scheduled?: Yes</p>
                    <p>IPs Excluded?: Yes</p>
                    <p>Time Started: 10:00:00 AM - 9/12/2024</p>
                    <p>Time Completed: </p>
                    <button on:click={() => logButtonClick('Dummy button clicked')}>Click Me</button>
                    <button on:click={downloadLogs}>Download Logs</button>
                    <p> {timestamp}</p>
                </div>
            
            </div>

            <!-- Entry Points dropdown section -->
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
            <!-- View Results button -->
            <div id="viewResults" class="my-6">
                <button type="button" class="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
                    View Results
                </button>
            </div>
        </div>

        <div id="middle" class="flex-top float-left  w-8/12  py-0">
            <!-- start of Summary-->
            <div id="bottomSettings" class="py-8 shadow-2xl dark:bg-gray-900"> 
                <h2 class="text-center font-bold text-xl leading-none text-gray-900 dark:text-white me-1 dark:bg-gray-900" >Summary</h2>
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