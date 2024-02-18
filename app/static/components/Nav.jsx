const Nav = () => {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-primary rounded-bottom-left rounded-bottom-right">
            <a className="navbar-brand text-white display-1" href="/">
                3DVisSys
            </a>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown"
                aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                <span className="fa fa-bars text-white"></span>
            </button>
            <div className="collapse navbar-collapse justify-content-end pt-1 pb-1" id="navbarNavDropdown">
                <ul className="navbar-nav">
                    <li className="nav-item active">
                        <a className="nav-link bg-primary text-white" href="/">
                            Home <span className="sr-only">(current)</span>
                        </a>
                    </li>
                    <li className="nav-item dropdown">
                        <a className="nav-link dropdown-toggle bg-primary text-white" href="#" id="navbarDropdownMenuLink"
                            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            Data
                        </a>
                        <div className="dropdown-menu bg-primary" aria-labelledby="navbarDropdownMenuLink">
                            <a className="dropdown-item text-white" href="https://mrms.ncep.noaa.gov/data/" target="_blank">
                                NOAA MRMS</a>
                            <a className="dropdown-item text-white" href="https://nominatim.org/release-docs/latest/api/Overview/"
                                target="_blank">
                                OpenStreetMap</a>
                        </div>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link bg-primary text-white" target="_blank" href="https://github.com/lanceu0128/3dvissys">
                            <span className="fab fa-github"></span>
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link bg-primary text-white" href="mailto:marulraj@umd.edu?cc=lpu@umd.edu">
                            <span className="fa fa-envelope"></span>
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
    )
}

ReactDOM.render(<Nav />, document.querySelector('#nav'));
