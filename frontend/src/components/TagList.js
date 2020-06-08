import React from "react";
const TagListBody = (props) => {
  const rows = props.tagListData.map((row, index) => {
    return (
      <div className="tag-grid">
        <h5 key={index}>{row}</h5>
      </div>
    );
  });
  return <div>{rows}</div>;
};
const TagList = (props) => {
  const { tagListData } = props;
  return <TagListBody tagListData={tagListData} />;
};
export default TagList;
