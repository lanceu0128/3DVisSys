const LoadingModal = () => {
    const [elapsedTime, setElapsedTime] = React.useState(0);

    React.useEffect(() => {
        setInterval(() => {
            setElapsedTime(prevElapsedTime => prevElapsedTime + 1);
        }, 1000);

        return () => {
            clearInterval(interval);
            setElapsedTime(0);
            // TODO: Fix glitch with elapsedTime starting at page load instead of show
        }
    }, []);

    return (
        <div className="modal fade" id="loading-modal">
            <div className="modal-dialog modal-dialog-centered">
                <div className="modal-content">
                    <div className="modal-body py-5">
                        <h1 id='loading-icon' className="modal-title text-center">⛈️</h1>
                        <h4 id='loading-text' className="modal-title text-center">
                            Loading... ({elapsedTime}s)
                        </h4>
                    </div>
                </div>
            </div>
        </div>
    );
};

ReactDOM.render(<LoadingModal />, document.querySelector('#modalContainer'));
