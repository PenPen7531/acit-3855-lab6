import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointAudit() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null);
    const [index, setIndex] = useState(null);
	const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store

    const getAudit = () => {
        fetch(`http://acit-3855-kakfa-jwang.eastus.cloudapp.azure.com:8120/health`)
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
        
        return (
            <div>
                <h3>Health Status</h3>
                {JSON.stringify(log)}
            </div>
        )
    }
}