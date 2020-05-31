import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
const EntryListBody = (props) => {
  const rows = props.entryData.map((row, index) => {
    return (
      <Link className="entry-block" to={{pathname:
        `/entry/${row._id}`,
      }}>
        {row.title}
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
