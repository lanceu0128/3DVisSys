const Nav = () => {
    return (
        <div>
            <nav className="navbar navbar-expand-lg navbar-light bg-primary">
                <a className="navbar-brand text-white display-1" href="/">
                    3DVisSys
                </a>
                <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown"
                    aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="fa fa-bars text-white"></span>
                </button>
                <div className="collapse navbar-collapse justify-content-end pt-1 pb-1" id="navbarNavDropdown">
                    <ul className="navbar-nav">
                        <li className="nav-item active mx-1">
                            <a className="nav-link rounded bg-primary text-white" href="/">
                                Home <span className="sr-only">(current)</span>
                            </a>
                        </li>
                        <li className="nav-item dropdown mx-1">
                            <a className="nav-link rounded dropdown-toggle bg-primary text-white" href="#" id="navbarDropdownMenuLink"
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
                        <li className="nav-item mx-1">
                            <a className="nav-link rounded bg-primary text-white" target="_blank" href="https://github.com/lanceu0128/3dvissys">
                                <span className="fab fa-github"></span>
                            </a>
                        </li>
                        <li className="nav-item mx-1">
                            <a className="nav-link rounded bg-primary text-white" href="mailto:marulraj@umd.edu?cc=lpu@umd.edu">
                                <span className="fa fa-envelope"></span>
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>
        </div>
    )
}

ReactDOM.render(<Nav />, document.querySelector('#nav'));
