import React from "react";

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-content">
        <div className="footer-left">
          <span className="project-title-footer">Product Sentiment Analyzer & Review Dashboard</span>
          <span className="college-name-footer">College of Engineering & Technology</span>
        </div>
        <div className="footer-right">
          <span className="team-info-footer">Developed by Team Frontend (Narmadha)</span>
          <span className="copyright-footer">
            &copy; {currentYear} Major Project. All Rights Reserved.
          </span>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
