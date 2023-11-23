import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointAudit() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState({});
    const [error, setError] = useState(null);
    
    const getAudit = () => {
        fetch(`http://acit-3855-kakfa-jwang.eastus.cloudapp.azure.com/health/`)
            .then(res => res.json())
            .then((result)=>{
			
                setLog(result);
               
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
	useEffect(() => {
		const interval = setInterval(() => getAudit(), 1000); // Update every 1 seconds
		return() => clearInterval(interval);
    }, [getAudit]);

    if (error){
        return (<div className={"error"}>Error found when fetching from Health</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){


        // Get current seconds
        const date_now = new Date();

        // Get seconds from json data
        const date_before = new Date(log['last_updated']);
        const date_dif = Math.abs((date_before.getTime() - date_now.getTime()) / 1000);

        // console.log(date_now,  date_before);
        return (
            <div>
                <h1>Health Stats</h1>
                <table className={"StatsTable"}>
					<tbody>

						<tr>
							<td colspan="2">Receiver Status: {log['receiver']}</td>
                        </tr>
                        <tr>
							<td colspan="2">Storage Status: {log['storage']}</td>
						</tr>
						<tr>
							<td colspan="2">Processing Status: {log['processing']}</td>
						</tr>
						<tr>
							<td colspan="2">Audit Status: {log['audit']}</td>
						</tr>
						
					</tbody>
                </table>
                <h3>Last Updated: {log['last_updated']}</h3>
                
                <h3>Last Updated: {date_dif} Seconds Ago</h3>
            </div>
        )
    }
}