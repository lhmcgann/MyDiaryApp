import React from "react";
import { Link } from "react-router-dom";
// import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
const EntryListBody = (props) => {
  const rows = props.entryData.map((row, index) => {
    return (
      <Link className="entry-block" to={`/entry/${row.title}`}>
        {row.title}
        <br />
        {row.date}
      </Link>
    );
  });

  return <tbody>{rows}</tbody>;
};
const EntryList = (props) => {
  const { entryData } = props;

  return (
    <table>
      <EntryListBody entryData={entryData} />
    </table>
  );
};
export default EntryList;
