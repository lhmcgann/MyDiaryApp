import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
const EntryListBody = (props) => {
  const rows = props.entryData.map((row, index) => {
    return (
      <div className="centered" key={index}>
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

  return <div>{rows}</div>;
};
const EntryList = (props) => {
  const { entryData, removeEntry } = props;
  return <EntryListBody entryData={entryData} removeEntry={removeEntry} />;
};
export default EntryList;
