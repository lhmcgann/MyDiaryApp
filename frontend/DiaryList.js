import React, { Component } from "react";
import { Link } from "react-router-dom";

const DiaryListBody = (props) => {
  const rows = props.characterData.map((row, index) => {
    return (
      <div class="centered">
        <h5 key = {index}>
        <Link to={`/diary/${row.name}/${row.id}`}>
          <button class="diary-block">{row.name}</button>
        </Link>
        </h5>
      </div>
    );
  });
  return <tbody>{rows}</tbody>;
};
const DiaryListFooter = () => {
  return (
    <Link to="/new-diary/">
      <button class="diary-block">+ Add Diary</button>
    </Link>
  );
};
const DiaryList = (props) => {
  const { characterData } = props;

  return (
    <table>
      <DiaryListBody characterData={characterData} />
      <DiaryListFooter />
    </table>
  );
};
export default DiaryList;
