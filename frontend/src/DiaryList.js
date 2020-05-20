import React, { Component } from "react";
import { Link } from "react-router-dom";
const DiaryListBody = (props) => {
  const rows = props.characterData.map((row, index) => {
    return (
      <div class="centered">
        <h5 key={index}>
          <Link to={{ pathname: `/diary/${row._id}`, title: row.title }}>
            <button class="diary-block">{row.title}</button>
          </Link>
        </h5>
      </div>
    );
  });
  return <tbody>{rows}</tbody>;
};
const DiaryList = (props) => {
  const { characterData } = props;
  return (
    <table>
      <DiaryListBody characterData={characterData} />
    </table>
  );
};
export default DiaryList;
