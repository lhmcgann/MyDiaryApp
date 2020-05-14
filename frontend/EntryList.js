import React, { Component } from "react";
import { Link } from "react-router-dom";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
const EntryListBody = (props) => {
  const rows = props.entryData.map((row, index) => {
    return (
      <Link to="/entry/:id">
        <div class="entry-block">
          <button>{row.name}</button>
        </div>
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
