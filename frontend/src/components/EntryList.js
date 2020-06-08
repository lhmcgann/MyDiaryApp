import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
const EntryListBody = (props) => {
  const rows = props.entryData.map((row, index) => {
    return (
      <div>
        <Link
          className="entry-block"
          to={`${window.location.pathname}/entries/${row._id}`}
        >
          {row.title}
        </Link>
        <button onClick={() => props.removeEntry(index)}>Delete</button>
      </div>
    );
  });

  return <tbody>{rows}</tbody>;
};
const EntryList = (props) => {
  const { entryData, removeEntry } = props;
  return (
    <table>
      <EntryListBody entryData={entryData} removeEntry={removeEntry} />
    </table>
  );
};
export default EntryList;
