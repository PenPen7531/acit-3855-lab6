import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointAudit() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState({});
    const [error, setError] = useState(null);
    const [index, setIndex] = useState(null);
	const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
    
    const getAudit = () => {
        fetch(`http://acit-3855-kakfa-jwang.eastus.cloudapp.azure.com/health/`)
            .then(res => res.json())
            .then((result)=>{
			
                setLog(result);
                setIndex(rand_val)
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
	useEffect(() => {
		const interval = setInterval(() => getAudit(), 4000); // Update every 4 seconds
		return() => clearInterval(interval);
    }, [getAudit]);

    if (error){
        return (<div className={"error"}>Error found when fetching from Health</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        const date_now = new Date().getSeconds();
        const date_before = new Date(log['last_updated']).getSeconds();


        console.log(abs(date_now - date_before));
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

            </div>
        )
    }
}